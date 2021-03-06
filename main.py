import importlib
import os
import time

from tqdm import tqdm

from tools.Saver import Saver
from tools.Visualizer import Visualizer


def init_all():
    print("=> initializing. parsing arguments.")
    opts = importlib.import_module('options.custom-options')
    opt_init = opts.CustomOptions().opt

    data_lib = importlib.import_module('datasets')
    models_lib = importlib.import_module('models')
    criterions_lib = importlib.import_module('criterions')

    dataloader_init = data_lib.create_dataloader(opt_init)
    model_init = models_lib.create_model(opt_init)
    loss_init, metrics_init = criterions_lib.create_criterion(opt_init)
    return opt_init, dataloader_init, model_init, loss_init, metrics_init


if __name__ == '__main__':
    opt, dataloader, model, loss, metrics = init_all()
    visualizer = Visualizer(opt)
    saver = Saver(opt)
    # saver.latest()
    resume = os.path.dirname(opt.resume_path)
    for epoch in range(0, opt.epochs):
        epoch_start_time = time.time()
        epoch_iter = 0

        if opt.mode == "predict":
            model.load_model(store_path=os.path.join(resume, f"epoch_{epoch * 4}.pth"))
            res = model.predict_batch(inputs=None, loss=None, metrics=None, niter=None, epoch=None)
            visualizer.display_vis_loss(res, epoch, epoch)
            continue
        if opt.mode == "onnx":
            model.load_model(store_path=os.path.join(resume, "latest.pth"))
            res = model.frozen_onnx(resume)
            break

        for i, data in tqdm(enumerate(dataloader)):
            iter_start_time = time.time()
            niter = i + epoch * len(dataloader)

            # check if dataloader is right.
            # visualizer.display_vis_loss({"vis": {"Source": data["Source"]},
            #                              "loss": {}}, epoch, niter)
            if opt.mode == "train":
                res = model.train_batch(inputs=data, loss=loss, metrics=metrics, niter=niter, epoch=epoch)
                if niter % 20 != 0:
                    visualizer.display_vis_loss({
                        "vis": {},
                        "loss": res["loss"]
                    }, epoch, niter)
                else:
                    visualizer.display_vis_loss(res, epoch, niter)
                visualizer.print_current_errors(epoch, i, res["loss"], time.time() - iter_start_time)
            elif opt.mode == "test":
                pass
            else:
                pass

    #         if epoch % opt.display_freq == 0:
    #             save_result = epoch % opt.update_html_freq == 0
    #             visualizer.display_current_results(model.get_current_visuals(), epoch, save_result)
    #
    #         if epoch % opt.print_freq == 0:
    #             errors = model.get_current_errors()
    #             t = (time.time() - iter_start_time) / opt.batchSize
    #             visualizer.print_current_errors(epoch, epoch_iter, errors, t)
    #             if opt.display_id > 0:
    #                 visualizer.plot_current_errors(epoch, float(epoch_iter) / dataset_size, opt, errors)
    #
    #         if epoch % opt.save_latest_freq == 0:
    #             print('saving the latest model (epoch %d, total_steps %d)' %
    #                   (epoch, epoch))
    #             model.save('latest')
    #
    #     if epoch % opt.save_epoch_freq == 0:
    #         print('saving the model at the end of epoch %d, iters %d' %
    #               (epoch, epoch))
    #         model.save('latest')
    #         model.save(epoch)
    #
    #     print('End of epoch %d / %d \t Time Taken: %d sec' %
    #           (epoch, opt.niter + opt.niter_decay, time.time() - epoch_start_time))
    #     model.update_learning_rate()
